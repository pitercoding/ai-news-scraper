import Link from "next/link";

import { Article } from "@/types/article";

interface ArticleCardProps {
    article: Article;
}

export default function ArticleCard({
    article,
}: ArticleCardProps) {
    return (
        <article className="article-card">
            {article.category && (
                <span className="article-category">
                    {article.category}
                </span>
            )}

            <h2 className="article-title">
                {article.title}
            </h2>

            <p className="article-summary">
                {article.summary}
            </p>

            <div className="article-actions">
                <Link
                    className="article-link"
                    href={`/articles/${article.id}`}
                >
                    View details →
                </Link>

                <a
                    className="article-link article-external-link"
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Read original article →
                </a>
            </div>
        </article>
    );
}