import Link from "next/link";


export default function Header() {
    return (
        <header className="site-header">
            <div className="site-header-content">
                <Link
                    className="site-logo"
                    href="/"
                >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src="/logo.png"
                        alt=""
                        width={28}
                        height={28}
                        className="site-logo-icon"
                    />
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