import {Card} from '@/webcheck/components/Form/Card.tsx';
import Row, {type RowProps} from '@/webcheck/components/Form/Row.tsx';
import type {JSX} from "react";

const cardStyles = `
  grid-row: span 2;
  .content {
    max-height: 50rem;
    overflow-y: auto;
  }
`;

const PageResourcesCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
    const {data} = props;
    const resources = data?.resources || [];
    if (!data) {
        return null;
    }

    return (
        <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
            <div className="content">
                {
                    resources.length === 0 && <p>No resources detected.</p>
                }
                {
                    resources.map((row: any, index: number) => {
                        return (
                            <Row key={`${row.name}-${index}`} lbl={row.initiatorType} val={row.name}
                                 element={<a href={row.name} target={"_blank"} rel={"nofollow noreferer noopener"}>
                                     {row.name}</a> }/>
                        )
                    })
                }
                { data?.totalBytesTransferred && <Row lbl="Total Bytes Transfered" val={`${data.totalBytesTransferred} bytes`} /> }
                { data?.pageLoadTimeMs && <Row lbl="Load Time" val={`${data.pageLoadTimeMs} ms`} /> }
            </div>
        </Card>
    );
}

export default PageResourcesCard;
