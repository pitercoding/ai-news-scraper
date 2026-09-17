import Link from "next/link";


export default function Header() {
    return (
        <header className="site-header">
            <div className="site-header-content">
                <Link
                    className="site-logo"
                    href="/"
                >
                    AI News Scraper
                </Link>

                <nav>
                    <Link href="/">
                        Articles
                    </Link>
                </nav>
            </div>
        </header>
    );
}