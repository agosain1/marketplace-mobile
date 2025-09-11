import type { _TODO_LISTING_MODEL } from 'src/types';

/**
 * Mimics api call to get market listings
 */
export async function MOCK_API_CALL_GET_LISTINGS(): Promise<_TODO_LISTING_MODEL[]> {
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return Math.random() < 0.75
    ? Array.from({ length: 20 }).map((_, i) =>
        i % 2 === 0
          ? {
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
            }
          : {
              id: '2',
              title: 'Mountain Bike',
              description: 'A sturdy mountain bike suitable for all terrains.',
              price: 300.0,
              currency: 'USD',
              location: 'San Francisco, CA',
              images: ['/test2.png'],
              views: 85,
              created_at: new Date(),
              updated_at: new Date(),
              seller_id: 'user456',
              category: 'Sports',
              condition: 'poor',
              status: 'poor',
              latitude: 37.7749,
              longitude: -122.4194,
            },
      )
    : [];
}
