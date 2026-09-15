import ArticleCard from "@/components/ArticleCard";
import CategoryFilter from "@/components/CategoryFilter";
import SearchBar from "@/components/SearchBar";
import {
  getArticles,
  getCategories,
} from "@/services/articleService";


interface HomeProps {
  searchParams: Promise<{
    category?: string;
    search?: string;
  }>;
}


export default async function Home({
  searchParams,
}: HomeProps) {
  const params = await searchParams;

  const data = await getArticles({
    category: params.category,
    search: params.search,
  });

  const categories = await getCategories();

  return (
    <main>
      <h1>AI News Scraper</h1>

      <p>
        Total articles: {data.total}
      </p>

      <div className="article-controls">
        <SearchBar />

        <CategoryFilter
          categories={categories}
        />
      </div>

      <section>
        {data.items.map((article) => (
          <ArticleCard
            key={article.id}
            article={article}
          />
        ))}
      </section>
    </main>
  );
}