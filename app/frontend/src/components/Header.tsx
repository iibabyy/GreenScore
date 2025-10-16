import { Link } from "react-router-dom";
import greenbook_icon from "@/assets/greenbook_icon.png";
interface HeaderProps {
  title: string;
  subtitle: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  return (
    <header className="bg-background py-6 px-4 ">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          <div className="flex flex-row items-center ">
            <img src={greenbook_icon} alt="GreenBook" className="h-24" />
            <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          </div>
          <nav className="hidden md:block">
            <ul className="flex space-x-8">
              <li>
                <Link
                  to="/"
                  className="text-gray-600 hover:text-gray-900 font-medium lg:text-xl"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  to="/supplements"
                  className="text-gray-600 hover:text-gray-900 font-medium lg:text-xl"
                >
                  Supplements
                </Link>
              </li>
              <li>
                <Link
                  to="/favorites"
                  className="text-gray-600 hover:text-gray-900 font-medium lg:text-xl"
                >
                  Favoris
                </Link>
              </li>
              <li>
                <Link
                  to="/about"
                  className="text-gray-600 hover:text-gray-900 font-medium lg:text-xl"
                >
                  About
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
