import {
    ArticleDetails,
    ArticlePaginationResponse,
} from "@/types/article";


const API_URL = process.env.NEXT_PUBLIC_API_URL;


interface GetArticlesParams {
    category?: string;
    search?: string;
    limit?: number;
    offset?: number;
}


export async function getArticles(
    params?: GetArticlesParams,
): Promise<ArticlePaginationResponse> {
    const searchParams = new URLSearchParams();

    if (params?.category) {
        searchParams.set(
            "category",
            params.category,
        );
    }

    if (params?.search) {
        searchParams.set(
            "search",
            params.search,
        );
    }

    if (params?.limit !== undefined) {
        searchParams.set(
            "limit",
            params.limit.toString(),
        );
    }

    if (params?.offset !== undefined) {
        searchParams.set(
            "offset",
            params.offset.toString(),
        );
    }

    const queryString = searchParams.toString();

    const url = queryString
        ? `${API_URL}/articles?${queryString}`
        : `${API_URL}/articles`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Failed to fetch articles.");
    }

    return response.json();
}

export async function getCategories(): Promise<string[]> {
    const response = await fetch(`${API_URL}/categories`);

    if (!response.ok) {
        throw new Error("Failed to fetch categories.");
    }

    return response.json();
}

export async function getArticle(
    id: number,
): Promise<ArticleDetails> {
    const response = await fetch(`${API_URL}/articles/${id}`);

    if (!response.ok) {
        throw new Error("Failed to fetch article.");
    }

    return response.json();
}