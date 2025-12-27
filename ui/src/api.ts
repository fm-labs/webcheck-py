const API_BASE_URL = "http://localhost:8000/webcheck"

export const fetchWebcheckResults = async (domain: string) => {
    try {
        const response = await fetch(`${API_BASE_URL}/d/` + domain)
        const data = await response.json()
        console.log("Response data:", data)
        return data
    } catch (error) {
        console.error("Error fetching data:", error)
        throw error
    }
}

export const fetchRecentScans = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/scans/`)
        const data = await response.json()
        console.log("Response data:", data)
        return data
    } catch (error) {
        console.error("Error fetching data:", error)
        throw error
    }
}

export const postDomainScan = async (domain: string) => {
    try {
        const response = await fetch(`${API_BASE_URL}/d/` + domain, {
            method: "POST"
        })
        const data = await response.json()
        console.log("Response data:", data)
        return data
    } catch (error) {
        console.error("Error posting data:", error)
        throw error
    }
}

export const doCheck = async (checkName: string, domain: string) => {
    try {
        const response = await fetch(`${API_BASE_URL}/c/` + checkName + "/?domain=" + domain, {
            method: "POST"
        })
        const data = await response.json()
        console.log("Response data:", data)
        return data
    } catch (error) {
        console.error("Error fetching data:", error)
        throw error
    }
}
