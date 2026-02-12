import { useQuery } from '@tanstack/react-query';
import { athletesAPI } from '../lib/api';

export default function Athletes() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['athletes'],
    queryFn: async () => {
      const response = await athletesAPI.getAll();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading athletes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800">Error loading athletes: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Our Athletes</h1>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.map((athlete) => (
          <div key={athlete.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
            <h3 className="text-xl font-bold text-gray-900 mb-2">{athlete.name}</h3>
            <div className="space-y-1 text-gray-700">
              <p>
                <span className="font-semibold">Grade:</span> {athlete.grade}
              </p>
              <p>
                <span className="font-semibold">PR:</span> {athlete.personal_record}
              </p>
              <p>
                <span className="font-semibold">Team:</span> {athlete.team}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
