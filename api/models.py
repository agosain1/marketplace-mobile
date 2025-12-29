from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import ARRAY, Boolean, CheckConstraint, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class UsZipcodes(Base):
    __tablename__ = 'us_zipcodes'
    __table_args__ = (
        PrimaryKeyConstraint('zipcode', name='us_zipcodes_pkey'),
        Index('idx_us_zipcodes_city', 'city'),
        Index('idx_us_zipcodes_city_state', 'city', 'state_code'),
        Index('idx_us_zipcodes_lat_lng', 'latitude', 'longitude'),
        Index('idx_us_zipcodes_state', 'state')
    )

    zipcode: Mapped[str] = mapped_column(String(5), primary_key=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    latitude: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[decimal.Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    county: Mapped[Optional[str]] = mapped_column(String(100))
    county_code: Mapped[Optional[str]] = mapped_column(String(3))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('google_id', name='users_google_id_key'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_email', 'email', unique=True),
        Index('idx_users_google_id', 'google_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    fname: Mapped[str] = mapped_column(Text, nullable=False)
    lname: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    email_verified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    google_id: Mapped[Optional[str]] = mapped_column(String(255))
    pfp_url: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))

    listings: Mapped[list['Listings']] = relationship('Listings', back_populates='seller')
    messages: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.receiver_id]', back_populates='receiver')
    messages_: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.sender_id]', back_populates='sender')
    refresh_tokens: Mapped[list['RefreshTokens']] = relationship('RefreshTokens', back_populates='user')


class Listings(Base):
    __tablename__ = 'listings'
    __table_args__ = (
        CheckConstraint("condition::text = ANY (ARRAY['new'::character varying, 'used'::character varying, 'refurbished'::character varying]::text[])", name='listings_condition_check'),
        CheckConstraint("status::text = ANY (ARRAY['active'::character varying, 'sold'::character varying, 'archived'::character varying]::text[])", name='listings_status_check'),
        ForeignKeyConstraint(['seller_id'], ['users.id'], ondelete='CASCADE', name='fk_seller'),
        PrimaryKeyConstraint('id', name='listings_pkey'),
        Index('idx_listings_lat_lng', 'latitude', 'longitude')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'USD'::character varying"))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'active'::character varying"))
    views: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    seller_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    images: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(11, 8))
    location: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))

    seller: Mapped[Optional['Users']] = relationship('Users', back_populates='listings')


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        CheckConstraint('sender_id <> receiver_id', name='check_different_users'),
        ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE', name='fk_messages_receiver'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE', name='fk_messages_sender'),
        PrimaryKeyConstraint('id', name='messages_pkey'),
        Index('idx_messages_conversation', 'sender_id', 'receiver_id', 'created_at'),
        Index('idx_messages_created_at', 'created_at'),
        Index('idx_messages_receiver_id', 'receiver_id'),
        Index('idx_messages_sender_id', 'sender_id'),
        Index('idx_messages_unread', 'receiver_id', 'read_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    sender_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    receiver_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    receiver: Mapped['Users'] = relationship('Users', foreign_keys=[receiver_id], back_populates='messages')
    sender: Mapped['Users'] = relationship('Users', foreign_keys=[sender_id], back_populates='messages_')


class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='refresh_tokens_user_id_fkey'),
        PrimaryKeyConstraint('id', name='refresh_tokens_pkey'),
        Index('idx_refresh_tokens_expires_at', 'expires_at'),
        Index('idx_refresh_tokens_user_id', 'user_id'),
        Index('idx_refresh_tokens_user_revoked', 'user_id', 'revoked')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("(CURRENT_TIMESTAMP + '7 days'::interval)"))
    revoked: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='refresh_tokens')


class VerificationCodes(Base):
    __tablename__ = 'verification_codes'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='verification_codes_user_id_fkey'),
        PrimaryKeyConstraint('user_id', name='verification_codes_pkey'),
        Index('idx_verification_codes_code', 'code')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
