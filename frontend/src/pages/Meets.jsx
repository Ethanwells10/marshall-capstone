import { useQuery } from '@tanstack/react-query';
import { meetsAPI } from '../lib/api';

export default function Meets() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['meets'],
    queryFn: async () => {
      const response = await meetsAPI.getAll();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          <p className="mt-4 text-gray-600">Loading meet schedule...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800">Error loading meets: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Meet Schedule</h1>

      <div className="space-y-4">
        {data?.map((meet) => (
          <div key={meet.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{meet.name}</h3>
                <div className="space-y-1 text-gray-700">
                  <p>
                    <span className="font-semibold">Date:</span> {new Date(meet.date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                  <p>
                    <span className="font-semibold">Location:</span> {meet.location}
                  </p>
                  <p>
                    <span className="font-semibold">Distance:</span> {meet.distance}
                  </p>
                </div>
              </div>
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                {meet.distance}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
