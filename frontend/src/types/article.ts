export interface Article {
    id: number;
    title: string;
    url: string;
    published_at: string;
    summary: string;
    ai_summary: string | null;
    key_points: string[] | null;
    category: string | null;
}

export interface ArticleDetails extends Article {
    content: string;
}

export interface ArticlePaginationResponse {
    items: Article[];
    total: number;
    limit: number;
    offset: number;
}