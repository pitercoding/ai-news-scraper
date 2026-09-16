import ArticleCard from "@/components/ArticleCard";
import CategoryFilter from "@/components/CategoryFilter";
import SearchBar from "@/components/SearchBar";
import Pagination from "@/components/Pagination";
import {
  getArticles,
  getCategories,
} from "@/services/articleService";


interface HomeProps {
  searchParams: Promise<{
    category?: string;
    search?: string;
    page?: string;
  }>;
}


export default async function Home({
  searchParams,
}: HomeProps) {
  const params = await searchParams;

  const limit = 12;

  const page = Number(params.page) || 1;

  const offset = (page - 1) * limit;

  const data = await getArticles({
    category: params.category,
    search: params.search,
    limit,
    offset,
  });

  const totalPages = Math.ceil(
    data.total / limit,
  );

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

      {totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
        />
      )}
    </main>
  );
}