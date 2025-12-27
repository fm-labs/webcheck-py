import GraphVisualization from "@/graph-visualization.tsx";
import React from "react";
import ReactJson from "@microlink/react-json-view";
import {Card} from "@/webcheck/components/Form/Card.tsx";

const DomainNetwork = ({data}: { data: any }) => {

    const [graphdata, setGraphdata] = React.useState(null);

    const buildGraphData = React.useCallback(() => {
        if (!data) {
            return {nodes: [], edges: []};
        }

        console.log("Building graph data for:", data);
        const nodes = []
        const edges = []
        let idCounter = 1;
        nodes.push({
            id: idCounter,
            item_id: `domain-${idCounter}`,
            label: data.url,
            type: 'domain',
        })

        if (data?.parsed?.linkDomains && data?.parsed?.linkDomains.length > 0) {
            for (const linkedDomain of data.parsed.linkDomains) {
                idCounter += 1;
                nodes.push({
                    id: idCounter,
                    item_id: `domain-${idCounter}`,
                    label: linkedDomain,
                    type: 'linked-domain',
                })
            }
        }

        // Create edges from the main domain to each linked domain
        for (let i = 1; i < nodes.length; i++) {
            edges.push({
                id: `${1}->${nodes[i].id}`,
                from: 1,
                to: nodes[i].id,
                type: 'links-to',
            })
        }

        return {nodes, edges}
    }, [data]);

    React.useEffect(() => {
        // fetch('/graph.json')
        //     .then(response => response.json())
        //     .then(data => setAwsGraph(data))
        //     .catch(error => console.error('Error fetching graph data:', error));
        const data = buildGraphData();
        setGraphdata(data);
    }, [buildGraphData]);

    return <Card heading={"Domain Network Graph"}>
        <div>
            {data?.url}
            {graphdata && <GraphVisualization data={graphdata as any}/>}
        </div>
        {/*<ReactJson src={graphdata}/>*/}
    </Card>;
};

export default DomainNetwork;