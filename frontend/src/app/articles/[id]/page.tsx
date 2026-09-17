import Link from "next/link";
import { notFound } from "next/navigation";

import { getArticle } from "@/services/articleService";


interface ArticleDetailsPageProps {
    params: Promise<{
        id: string;
    }>;
}


export default async function ArticleDetailsPage({
    params,
}: ArticleDetailsPageProps) {
    const { id } = await params;

    let article;

    try {
        article = await getArticle(
            Number(id),
        );
    } catch {
        notFound();
    }

    return (
        <main className="article-details">
            <Link
                className="article-back-link"
                href="/"
            >
                ← Back to articles
            </Link>

            {article.category && (
                <span className="article-category">
                    {article.category}
                </span>
            )}

            <h1 className="article-details-title">
                {article.title}
            </h1>

            <p className="article-details-date">
                Published on{" "}
                {new Date(
                    article.published_at,
                ).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                })}
            </p>

            <p className="article-details-summary">
                {article.summary}
            </p>

            <section className="article-details-content">
                <h2>Article Content</h2>

                {article.content
                    .split(/\n+/)
                    .filter((paragraph) => paragraph.trim())
                    .map((paragraph, index) => (
                        <p key={index}>
                            {paragraph.trim()}
                        </p>
                    ))}
            </section>

            {article.ai_summary && (
                <section className="article-details-section article-ai-summary">
                    <h2>AI Summary</h2>

                    <p>{article.ai_summary}</p>
                </section>
            )}

            {article.key_points && (
                <section className="article-details-section">
                    <h2>Key Points</h2>

                    <ul>
                        {article.key_points.map(
                            (point) => (
                                <li key={point}>
                                    {point}
                                </li>
                            ),
                        )}
                    </ul>
                </section>
            )}

            <a
                className="article-link"
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
            >
                Read original article →
            </a>
        </main>
    );
}