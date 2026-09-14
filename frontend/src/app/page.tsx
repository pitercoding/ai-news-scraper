import { getArticles } from "@/services/articleService";
import ArticleCard from "@/components/ArticleCard";


export default async function Home() {
  const data = await getArticles();

  return (
    <main>
      <h1>AI News Scraper</h1>

      <p>
        Total articles: {data.total}
      </p>

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