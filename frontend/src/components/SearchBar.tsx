"use client";


import { useRouter, useSearchParams } from "next/navigation";


export default function SearchBar() {
    const router = useRouter();
    const searchParams = useSearchParams();

    const currentSearch =
        searchParams.get("search") ?? "";


    function handleSubmit(
        event: React.FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault();

        const formData = new FormData(
            event.currentTarget,
        );

        const search = formData
            .get("search")
            ?.toString()
            .trim() ?? "";

        const params = new URLSearchParams(
            searchParams.toString(),
        );

        if (search) {
            params.set("search", search);
        } else {
            params.delete("search");
        }

        router.push(`/?${params.toString()}`);
    }


    return (
        <form onSubmit={handleSubmit}>
            <input
                type="search"
                name="search"
                placeholder="Search articles..."
                defaultValue={currentSearch}
            />

            <button type="submit">
                Search
            </button>
        </form>
    );
}
