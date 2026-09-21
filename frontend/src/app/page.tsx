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

  const page = Math.max(1, Math.floor(Number(params.page)) || 1);

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
      <h1>Latest News</h1>

      <p>
        {data.total} articles
      </p>

      <div className="article-controls">
        <SearchBar />

        <CategoryFilter
          categories={categories}
        />
      </div>

      {data.items.length > 0 ? (
        <section>
          {data.items.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
            />
          ))}
        </section>
      ) : (
        <div className="empty-state">
          <h2>No articles found</h2>

          <p>
            Try changing your search or category
            filter.
          </p>
        </div>
      )}

      {totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
        />
      )}
    </main>
  );
}