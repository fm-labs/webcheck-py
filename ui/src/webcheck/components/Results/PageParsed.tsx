import {Card} from '@/webcheck/components/Form/Card.tsx';
import Row from '@/webcheck/components/Form/Row.tsx';
import type {JSX} from "react";

const cardStyles = `
  grid-row: span 2;
  .content {
    max-height: 50rem;
    overflow-y: auto;
  }
`;

const CONTENT_TYPES = ['links', 'images', 'scripts', 'stylesheets', 'videos', 'audios', 'fonts', 'documents', 'phones', 'emails'];


const PageParsedCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
    const {data} = props;
    const parsed = data?.parsed;
    console.log("Parsed Data:", parsed);
    if (!data || !parsed) {
        return null;
    }

    return (
        <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
            <div className="content">
                {parsed?.title && <Row lbl={"Title"} val={parsed.title} />}
                {parsed?.headings && Object.entries(parsed.headings).map(([key, value]) => {
                    return (value as Array<any>).map((heading: string, index: number) => (
                        <div style={{textAlign: "left", padding: "1px"}} key={`${key}-${index}`}>
                            {`[heading ${key}] `} {heading}
                        </div>
                    ))
                })}
                {parsed?.meta && Object.entries(parsed.meta).map(([key, value]) => {
                    return <div style={{textAlign: "left", padding: "1px"}} key={`${key}`}>
                            {`[meta ${key}] `} {value as string}
                        </div>
                })}
                {CONTENT_TYPES.map((type: string) => {
                    if (parsed[type]) {
                        return (parsed[type]).map((row: any, index: number) => {
                            const [url, title] = row
                            return (
                                <div style={{textAlign: "left", padding: "1px"}} key={url}>
                                    {`[${type}] `}
                                    {title ? `${title} - ` : ''}
                                    <a href={url} target={"_blank"} rel={"nofollow noreferer noopener"}>{url}</a>
                                </div>
                            )
                        })
                    }
                    return null;
                })}
                {parsed?.domains && parsed?.domains.map((d) => {
                    return (
                        <div style={{textAlign: "left", padding: "1px"}} key={d}>
                            {`[domain] `} {d} <a href={'/?domain=' + d} target={"_blank"} rel={"nofollow noreferer noopener"}> (scan)</a>
                        </div>
                    )
                })}
                {parsed?.linkDomains && parsed?.linkDomains.map((d) => {
                    return (
                        <div style={{textAlign: "left", padding: "1px"}} key={d}>
                            {`[link-domain] `} {d} <a href={'/?domain=' + d} target={"_blank"} rel={"nofollow noreferer noopener"}> (scan)</a>
                        </div>
                    )
                })}

                {data?.adblockDetections && data.adblockDetections.length > 0 && (
                    <>
                        <hr />
                        <div><strong>Adblock Detections: ({data.adblockDetections.length})</strong></div>
                        {data.adblockDetections.map((adblock: string, index: number) => (
                            <div style={{textAlign: "left", padding: "1px"}} key={`adblock-${index}`}>
                                [adblock] {adblock}
                            </div>
                        ))}
                    </>
                )}
                {data?.trackerDetections && data.trackerDetections.length > 0 && (
                    <>
                        <hr />
                        <div><strong>Tracking Detections: ({data.trackerDetections.length})</strong></div>
                        {data.trackerDetections.map((tracking: string, index: number) => (
                            <div style={{textAlign: "left", padding: "1px"}} key={`tracking-${index}`}>
                                [tracker] {tracking}
                            </div>
                        ))}
                    </>
                )}
                {data?.cookiebannerDetections && data.cookiebannerDetections.length > 0 && (
                    <>
                        <hr />
                        <div><strong>Cookie Banner Detections:</strong></div>
                        {data.cookiebannerDetections.map((privacy: string, index: number) => (
                            <div style={{textAlign: "left", padding: "1px"}} key={`privacy-${index}`}>
                                [cookiebanner] {privacy}
                            </div>
                        ))}
                    </>
                )}
            </div>
        </Card>
    );
}

export default PageParsedCard;
