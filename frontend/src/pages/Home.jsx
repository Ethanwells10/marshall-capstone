export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Jones County Cross Country
          </h1>
          <p className="text-xl text-gray-600">
            Excellence in Running. Pride in Performance.
          </p>
        </div>

        {/* Welcome Card */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to Our Team
          </h2>
          <p className="text-gray-700 mb-4">
            The Jones County Cross Country team represents the pinnacle of athletic
            dedication and competitive spirit. Our runners train year-round to compete
            at the highest levels, pushing their limits and achieving personal bests.
          </p>
          <p className="text-gray-700">
            Explore our site to learn more about our talented athletes, upcoming meets,
            and race results throughout the season.
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-blue-50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-blue-900 mb-2">Our Athletes</h3>
            <p className="text-gray-700 mb-4">
              Meet the runners who make up our competitive team.
            </p>
            <a href="/athletes" className="text-blue-600 hover:text-blue-800 font-semibold">
              View Athletes →
            </a>
          </div>

          <div className="bg-green-50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-green-900 mb-2">Meet Schedule</h3>
            <p className="text-gray-700 mb-4">
              Check out our upcoming races and competitions.
            </p>
            <a href="/meets" className="text-green-600 hover:text-green-800 font-semibold">
              View Schedule →
            </a>
          </div>

          <div className="bg-purple-50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-purple-900 mb-2">Race Results</h3>
            <p className="text-gray-700 mb-4">
              See how our athletes performed in recent meets.
            </p>
            <a href="/results" className="text-purple-600 hover:text-purple-800 font-semibold">
              View Results →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
