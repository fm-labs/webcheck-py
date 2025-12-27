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

const RobotsTxtCard = (props: { data: { rules: RowProps[], sitemaps: RowProps[] }, title: string, actionButtons: any }): JSX.Element => {
    const {data} = props;
    const rules = data?.rules || [];
    const sitemaps = data?.sitemaps || [];
    if (!data) {
        return null;
    }

    return (
        <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
            <div className="content">
                {
                    rules.length === 0 && <p>No crawl rules found.</p>
                }
                {
                    rules.map((row: RowProps, index: number) => {
                        return (
                            <Row key={`${row.lbl}-${index}`} lbl={row.lbl} val={row.val}/>
                        )
                    })
                }
            </div>
            <div className="content">
                {
                    sitemaps.length === 0 && <p>No sitemaps found.</p>
                }
                {
                    sitemaps.map((row: RowProps, index: number) => {
                        return (
                            <Row key={`${row.lbl}-${index}`} lbl={row.lbl} val={row.val}/>
                        )
                    })
                }
            </div>
        </Card>
    );
}

export default RobotsTxtCard;
