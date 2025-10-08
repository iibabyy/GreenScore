export const scoreStyle = (letter: string) => {
  const map: Record<string, { badge: string; ring: string; primary: string }> = {
    A: { badge: 'bg-green-100 text-green-800', ring: '#10B981', primary: 'text-green-800' },
    B: { badge: 'bg-blue-100 text-blue-800', ring: '#3B82F6', primary: 'text-blue-800' },
    C: { badge: 'bg-yellow-100 text-yellow-800', ring: '#F59E0B', primary: 'text-yellow-800' },
    D: { badge: 'bg-orange-100 text-orange-800', ring: '#F97316', primary: 'text-orange-800' },
    E: { badge: 'bg-red-100 text-red-800', ring: '#EF4444', primary: 'text-red-800' },
  };
  return map[letter] || map['C'];
};
