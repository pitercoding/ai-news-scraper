import { Article } from "@/types/article";

interface ArticleCardProps {
    article: Article;
}

export default function ArticleCard({
    article,
}: ArticleCardProps) {
    return (
        <article>
            <h2>{article.title}</h2>

            {article.category && (
                <p>
                    Category: {article.category}
                </p>
            )}

            <p>{article.summary}</p>
        </article>
    );
}