"use client";


import { useRouter, useSearchParams } from "next/navigation";


interface CategoryFilterProps {
    categories: string[];
}


export default function CategoryFilter({
    categories,
}: CategoryFilterProps) {
    const router = useRouter();
    const searchParams = useSearchParams();

    const selectedCategory =
        searchParams.get("category") ?? "";


    function handleCategoryChange(
        event: React.ChangeEvent<HTMLSelectElement>,
    ) {
        const category = event.target.value;

        const params = new URLSearchParams(
            searchParams.toString(),
        );

        if (category) {
            params.set("category", category);
        } else {
            params.delete("category");
        }

        router.push(`/?${params.toString()}`);
    }


    return (
        <select
            value={selectedCategory}
            onChange={handleCategoryChange}
        >
            <option value="">
                All categories
            </option>

            {categories.map((category) => (
                <option
                    key={category}
                    value={category}
                >
                    {category}
                </option>
            ))}
        </select>
    );
}
