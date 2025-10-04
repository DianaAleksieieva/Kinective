export default function FoodPage() {
  return (
    <div className="p-6">
      <h2 className="text-3xl font-bold text-neonGreen mb-4 text-center">Food & Nutrition</h2>
      <p className="text-base text-neonPurple mb-6 text-center">
        Upload meals, count calories, and get nutrition advice 🍎
      </p>

      <div className="flex flex-col gap-4">
        <div className="p-4 bg-black border border-neonGreen rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-neonPurple mb-2">🥗 Healthy Meals</h3>
          <p className="text-sm">Discover easy recipes tailored to your goals.</p>
        </div>
        <div className="p-4 bg-black border border-neonPurple rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-neonGreen mb-2">🍔 Food Insights</h3>
          <p className="text-sm">Scan dishes and learn how they impact your health.</p>
        </div>
      </div>
    </div>
  );
}
