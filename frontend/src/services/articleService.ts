import { ArticlePaginationResponse } from "@/types/article";

const API_URL = process.env.NEXT_PUBLIC_API_URL;


export async function getArticles(): Promise<ArticlePaginationResponse> {
    const response = await fetch(`${API_URL}/articles`);

    if (!response.ok) {
        throw new Error("Failed to fetch articles.");
    }

    return response.json();
}