import React from 'react';
import HeadersCard from "@/webcheck/components/Results/Headers.tsx";
import HstsCard from "@/webcheck/components/Results/Hsts.tsx";
import HttpSecurityCard from "@/webcheck/components/Results/HttpSecurity.tsx";
import RobotsTxtCard from "@/webcheck/components/Results/RobotsTxt.tsx";
import SecurityTxtCard from "@/webcheck/components/Results/SecurityTxt.tsx";
import SitemapCard from "@/webcheck/components/Results/Sitemap.tsx";
import ScreenshotCard from "@/webcheck/components/Results/Screenshot.tsx";
import FirewallCard from "@/webcheck/components/Results/Firewall.tsx";
import DnsRecordsCard from "@/webcheck/components/Results/DnsRecords.tsx";
import ServerLocationCard from "@/webcheck/components/Results/ServerLocation.tsx";
import RedirectsCard from "@/webcheck/components/Results/Redirects.tsx";
import ServerStatusCard from "@/webcheck/components/Results/ServerStatus.tsx";
import Columns from "@/webcheck/components/Form/Columns.tsx";
import ReactJson from "@microlink/react-json-view";
import SocialTags from "@/webcheck/components/Results/SocialTags.tsx";
import SocialTagsCard from "@/webcheck/components/Results/SocialTags.tsx";
import WhoIsCard from "@/webcheck/components/Results/WhoIs.tsx";
import DomainLookupCard from "@/webcheck/components/Results/DomainLookup.tsx";
import PageResourcesCard from "@/webcheck/components/Results/PageResources.tsx";
import PageParsedCard from "@/webcheck/components/Results/PageParsed.tsx";
import TechStackCard from "@/webcheck/components/Results/TechStack.tsx";
import MailConfigCard from "@/webcheck/components/Results/MailConfig.tsx";
import SslCertCard from "@/webcheck/components/Results/SslCert.tsx";
import CarbonCard from "@/webcheck/components/Results/CarbonFootprint.tsx";
import DomainNetwork from "@/DomainNetwork.tsx";
import RankCard from "@/webcheck/components/Results/Rank.tsx";
import SslQualysCard from "@/webcheck/components/Results/SslQualys.tsx";


const WebcheckItem = ({domain, name, label, component: Component, data}: {
    domain: string,
    name: string;
    label: string;
    component: React.ComponentType<any>;
    data?: any
}) => {

    const [componentData, setComponentData] = React.useState<any>(data || null);

    React.useEffect(() => {
        setComponentData(data)
    }, [data])

    // React.useEffect(() => {
    //     if (componentData === null && domain) {
    //         // Fetch data for the component if not provided
    //         doCheck(name, domain)
    //             .then(setComponentData)
    //             .catch((e) => setComponentData({error: e?.e.message || 'Unknown error'}));
    //     }
    // }, [componentData, domain, name]);

    return (
        <div>
            <Component
                key={name}
                data={componentData}
                title={label}
                actionButtons={null}
            />
            {/*<div style={{backgroundColor: "#CCC", textAlign: "left"}}>
                <ReactJson src={componentData} name={false} collapsed={true} enableClipboard={false} displayDataTypes={false} />
            </div>*/}
        </div>
    );
}

const WebcheckResults = ({domain, results}: { domain: string, results: any }) => {

    const CHECKS = [
        {name: 'status', label: 'Status', component: ServerStatusCard},
        {name: 'server_location', label: 'Server Location', component: ServerLocationCard},
        {name: 'content', label: 'Headers', component: HeadersCard},
        {name: 'http_security', label: 'HTTP Security', component: HttpSecurityCard},
        {name: 'ssl', label: 'SSL Cert', component: SslCertCard},
        {name: 'hsts', label: 'HSTS', component: HstsCard},
        {name: 'whois', label: 'WHOIS', component: DomainLookupCard},
        {name: 'dns', label: 'DNS', component: DnsRecordsCard},
        {name: 'mx', label: 'Mail Config', component: MailConfigCard},
        {name: 'firewall', label: 'Firewall', component: FirewallCard},
        {name: 'robotstxt', label: 'Robots TXT', component: RobotsTxtCard},
        {name: 'securitytxt', label: 'Security TXT', component: SecurityTxtCard},
        {name: 'screenshot', label: 'Screenshot', component: ScreenshotCard},
        {name: 'sitemap', label: 'Sitemap', component: SitemapCard},
        {name: 'redirects', label: 'Redirects', component: RedirectsCard},
        {name: 'social_tags', label: 'Social Tags', component: SocialTagsCard},
        {name: 'wappalyzer', label: 'Tech Stack', component: TechStackCard},
        {name: 'page', label: 'Resources', component: PageResourcesCard},
        {name: 'carbon', label: 'Carbon Footprint', component: CarbonCard},
        //{ name: 'ssl_qualys', label: 'Qualys SSL Check', component: SslQualysCard },
        //{ name: 'umbrella_rank', label: 'Umbrella Rank', component: RankCard },
        //{ name: 'tranco_rank', label: 'Tranco Rank', component: RankCard },
    ]

    if (results?.error) {
        return (
            <div>
                <h2><a href={'https://' + domain}>{domain}</a></h2>
                <p style={{color: 'red'}}>Error: {results.error}</p>
            </div>
        );
    }

    // if (results?.status && results.status !== 'completed') {
    //     return (
    //         <div>
    //             <h2>{domain}</h2>
    //             <p>Status: {results.status}</p>
    //         </div>
    //     );
    // }

    return (
        <div>
            <h2><a target={"_blank"} rel={"noreferrer"} href={'https://' + domain}>{domain}</a></h2>
            <Columns>
                {CHECKS.map((check) => {
                    return (
                        <WebcheckItem
                            key={check.name}
                            label={check.label}
                            name={check.name}
                            component={check.component}
                            domain={domain}
                            data={results[check.name] || {}}
                        />
                    );
                })}
            </Columns>

            <h2>Content analysis</h2>
            <WebcheckItem domain={domain}
                          name={"content"}
                          label={"Content"}
                          component={PageParsedCard}
                          data={results['page'] || {}}/>

            <DomainNetwork data={results['page'] || {}}/>
        </div>
    );
};

export default WebcheckResults;