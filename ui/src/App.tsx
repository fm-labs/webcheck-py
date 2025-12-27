import * as React from 'react'
import './App.css'
import {fetchRecentScans, postDomainScan} from "@/api.ts";
import WebcheckResults from "@/WebcheckResults.tsx";
import {Card} from "@/webcheck/components/Form/Card.tsx";
import Heading from "@/webcheck/components/Form/Heading.tsx";
import {Helmet} from "react-helmet-async";

function App() {
    const [inputText, setInputText] = React.useState("")
    const [domain, setDomain] = React.useState<string>(null)
    const [resultJson, setResultJson] = React.useState(null)
    const [recentDomains, setRecentDomains] = React.useState<string[]>([])

    const urlQuery = React.useMemo(() => {
        return new URLSearchParams(window.location.search);
    }, []);

    React.useEffect(() => {
        const domainParam = urlQuery.get("domain")
        if (domainParam) {
            setDomain(domainParam)
            setInputText(domainParam)
        }
    }, [urlQuery]);

    React.useEffect(() => {
        const onPopState = (event) => {
            // This fires when user presses Back/Forward or history.go()
            console.log("popstate:", event.state);

            if (event.state?.domain) {
                console.log("Restoring domain from history state:", event.state.domain);
                setDomain(event.state.domain)
                setInputText(event.state.domain)
                setResultJson(null)
            }
        };
        window.addEventListener("popstate", onPopState);

        return () => {
            window.removeEventListener("popstate", onPopState);
        };
    }, []);

    React.useEffect(() => {
        const timer = setInterval(() => {
            fetchRecentScans().then((data) => setRecentDomains(data.domains || []))
        }, 30000);
        fetchRecentScans().then((data) => setRecentDomains(data.domains || []))
        return () => clearInterval(timer);
    }, [])

    // const updateHistoryWithDomain = (domain: string) => {
    //     const newUrl = new URL(window.location.href);
    //     newUrl.searchParams.set("domain", domain);
    //     window.history.pushState({"domain": domain}, '', newUrl.toString());
    // }

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputText(event.target.value)
    }

    // const handleFetchResultsClick = (event: React.FormEvent<HTMLButtonElement>) => {
    //     event.preventDefault()
    //     console.log("Submitted domain:", inputText)
    //     setDomain(inputText)
    //     updateHistoryWithDomain(inputText)
    //
    //     setResultJson({scan: {status: "fetching", message: "Fetching results..."}})
    //     fetchWebcheckResults(inputText)
    //         .then(data => {
    //             console.log("Response data:", data)
    //             setResultJson(data)
    //         })
    //         .catch(error => {
    //             console.error("Error fetching data:", error)
    //             setResultJson({error: "Failed to fetch data"})
    //         })
    // }

    const handleSubmitScanClick = (event: React.FormEvent<HTMLButtonElement>) => {
        event.preventDefault()
        console.log("Submitted domain for scan:", inputText)
        setDomain(null)
        if (inputText) {
            setDomain(inputText)
        }

        setResultJson({scan: {status: "submitted", message: "Scan submitted, waiting for results..."}})
        postDomainScan(inputText)
            .then(data => {
                console.log("Response data:", data)
                setResultJson(data)
            })
            .catch(error => {
                console.error("Error posting data:", error)
                setResultJson({error: "Failed to post data"})
            })
    }

    return (
        <>
            <Helmet>
                <title>{`${domain || "New scan"} | webcheck`}</title>
            </Helmet>
            <h1>webcheck</h1>
            <div className={"card"}>
                <p>Enter domain name to scan:{' '}</p>
                <div style={{display: "flex", gap: "0.5rem", alignItems: "center", justifyContent: "center"}}>
                    <input type="text" value={inputText} onChange={handleInputChange}/>

                    <button onClick={handleSubmitScanClick}>
                        Scan
                    </button>
                </div>
            </div>

            {resultJson && resultJson?.scan?.status === "completed" && <WebcheckResults domain={domain} results={resultJson}/>}

            {resultJson && resultJson?.scan?.status === "completed" && <Card styles={"margin-top: 1rem;"}>
                <Heading>Full Scan Result</Heading>
                <pre style={{
                    textAlign: "left",
                    maxWidth: "800px",
                    maxHeight: "600px",
                    overflow: "scroll"
                }}>{resultJson ? JSON.stringify(resultJson, null, 2) : "No results yet."}</pre>
            </Card>}

            {resultJson && resultJson?.scan && (
                <Card styles={"margin-top: 1rem; text-align: left;"}>
                    <Heading>Scan Status: {resultJson.scan.status}</Heading>
                    Message: {resultJson.scan.message}
                </Card>
            )}

            {recentDomains.length > 0 && <Card styles={"margin-top: 1rem;"}>
                <Heading>Recent Scans</Heading>
                <div style={{textAlign: "left"}}>
                    {recentDomains.map((d, index) => (
                        <div key={index}>
                            <a href={"?domain=" + encodeURIComponent(d)}>{d}</a>
                        </div>
                    ))}
                </div>
            </Card>}
        </>
    )
}

export default App
