import type { _TODO_LISTING_MODEL } from 'src/types';

/**
 * Mimics api call to get one listing information
 */
export async function MOCK_API_CALL_GET_LISTING(): Promise<_TODO_LISTING_MODEL> {
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    listing: {
      id: '1',
      title: 'Vintage Camera',
      description: 'A classic film camera in excellent condition.',
      price: 120,
      currency: 'USD',
      category: 'Electronics',
      location: 'New York, NY',
      images: ['/test0.png', '/test1.png', '/test2.png'],
      views: 120,
      created_at: new Date(),
      updated_at: new Date(),
      seller_id: 'user123',
      condition: 'poor',
      status: 'poor',
      latitude: 37.7749,
      longitude: -122.4194,
    },
    seller: {
      email: '',
      fname: 'Arnav',
      lname: 'Gosain',
      id: '1',
      created_at: new Date(),
      email_verified: true,
      google_id: '1',
      is_admin: true,
      password: 'why are we returning passwords',
      updated_at: new Date(),
    },
  };
}
