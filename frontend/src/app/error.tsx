"use client";


interface ErrorPageProps {
    error: Error & {
        digest?: string;
    };
    reset: () => void;
}


export default function ErrorPage({
    reset,
}: ErrorPageProps) {
    return (
        <main className="error-page">
            <h1>Something went wrong</h1>

            <p>We couldn&apos;t load the articles. Please try again.</p>

            <button
                type="button"
                onClick={reset}
            >
                Try again
            </button>
        </main>
    );
}