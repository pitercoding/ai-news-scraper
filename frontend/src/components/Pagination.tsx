"use client";


import { useRouter, useSearchParams } from "next/navigation";


interface PaginationProps {
    currentPage: number;
    totalPages: number;
}


export default function Pagination({
    currentPage,
    totalPages,
}: PaginationProps) {
    const router = useRouter();
    const searchParams = useSearchParams();


    function goToPage(page: number) {
        const params = new URLSearchParams(
            searchParams.toString(),
        );

        if (page === 1) {
            params.delete("page");
        } else {
            params.set("page", page.toString());
        }

        router.push(`/?${params.toString()}`, {
            scroll: false,
        });
    }


    return (
        <nav className="pagination">
            <button
                type="button"
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
            >
                Previous
            </button>

            <span>
                Page {currentPage} of {totalPages}
            </span>

            <button
                type="button"
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
            >
                Next
            </button>
        </nav>
    );
}