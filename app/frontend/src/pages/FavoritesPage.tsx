import { Link } from 'react-router-dom';

const FavoritesPage = () => {
  // Dans une vraie application, on récupérerait les favoris via un contexte ou une API
  // const { favorites } = useFavorites();
  const favorites = []; // Pour l'instant, on utilise un tableau vide

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Mes Favoris</h1>
      
      {favorites.length === 0 ? (
        <div className="text-center py-12">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-24 w-24 mx-auto text-gray-300 mb-4" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <p className="text-xl text-gray-600 mb-4">Vous n'avez pas encore de favoris</p>
          <p className="text-gray-500 mb-6">Commencez à explorer les compléments et ajoutez-les à vos favoris pour les retrouver facilement.</p>
          <Link 
            to="/supplements" 
            className="inline-block bg-accent text-gray-900 font-medium py-2 px-6 rounded hover:bg-secondary transition-colors"
          >
            Explorer les compléments
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Ici, on afficherait les cartes des compléments favoris */}
          <p>Contenu des favoris</p>
        </div>
      )}
    </div>
  );
};

export default FavoritesPage;