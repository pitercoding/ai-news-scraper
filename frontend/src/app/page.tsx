import ArticleCard from "@/components/ArticleCard";
import CategoryFilter from "@/components/CategoryFilter";
import {
  getArticles,
  getCategories,
} from "@/services/articleService";

interface HomeProps { 
  searchParams: Promise<{ 
    category?: string;
  }>;
}

export default async function Home({
  searchParams,
}: HomeProps) {
  const params = await searchParams;
  
  const data = await getArticles({
    category: params.category,
  });

  const categories = await getCategories();

  return (
    <main>
      <h1>AI News Scraper</h1>

      <p>
        Total articles: {data.total}
      </p>

      <CategoryFilter
        categories={categories}
      />

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