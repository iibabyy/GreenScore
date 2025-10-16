import { Link } from "react-router-dom";
import RotatingEarth from "@/components/ui/wireframe-dotted-globe";

const HomePage = () => {
  return (
    <div className="px-4 first-line:py-6 lg:py-12 sm:px-0 ">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center mb-12">
        <div className="text-center lg:text-left">
          <p className="text-xl lg:text-5xl font-medium text-gray-800 leading-10">
            Evaluate the environmental impact of dietary supplements and make
            informed choices for your health and the planet.
          </p>
        </div>
        <div className="hidden lg:block w-full">
          <RotatingEarth
            className="w-full max-w-[520px] mx-auto"
            width={520}
            height={380}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Search</h2>
          <p className="text-gray-600 mb-4">
            Find dietary supplements by name, brand, or ingredient.
          </p>
          <Link
            to="/supplements"
            className="inline-block bg-accent text-gray-900 font-medium py-2 px-4 rounded hover:bg-secondary transition-colors"
          >
            Explore
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Evaluation</h2>
          <p className="text-gray-600 mb-4">
            Discover detailed environmental scores for each product.
          </p>
          <Link
            to="/supplements"
            className="inline-block bg-accent text-gray-900 font-medium py-2 px-4 rounded hover:bg-secondary transition-colors"
          >
            View ratings
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Favorites</h2>
          <p className="text-gray-600 mb-4">
            Save your favorite supplements for quick access.
          </p>
          <Link
            to="/favorites"
            className="inline-block bg-accent text-gray-900 font-medium py-2 px-4 rounded hover:bg-secondary transition-colors"
          >
            View my favorites
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-semibold mb-4 text-center">
          How does it work?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-accent w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">1</span>
            </div>
            <h3 className="text-lg font-medium mb-2">Search</h3>
            <p className="text-gray-600">
              Find the dietary supplement you need
            </p>
          </div>
          <div className="text-center">
            <div className="bg-accent w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">2</span>
            </div>
            <h3 className="text-lg font-medium mb-2">Evaluate</h3>
            <p className="text-gray-600">
              Explore its detailed environmental impact
            </p>
          </div>
          <div className="text-center">
            <div className="bg-accent w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">3</span>
            </div>
            <h3 className="text-lg font-medium mb-2">Compare</h3>
            <p className="text-gray-600">Compare scores with other products</p>
          </div>
          <div className="text-center">
            <div className="bg-accent w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">4</span>
            </div>
            <h3 className="text-lg font-medium mb-2">Choose</h3>
            <p className="text-gray-600">
              Make an informed choice for your health and the planet
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
