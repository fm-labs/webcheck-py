import colors from '@/webcheck/styles/colors.ts';
import {Card} from '@/webcheck/components/Form/Card.tsx';
import Row from '@/webcheck/components/Form/Row.tsx';
import type {JSX} from "react";

const cardStyles = `
span.val {
  &.up { color: ${colors.success}; }
  &.down { color: ${colors.danger}; }
}
`;

const ServerStatusCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
    const serverStatus = props.data;
    if (!serverStatus) {
        return null
    }

    return (
        <Card heading={props.title.toString()} actionButtons={props.actionButtons} styles={cardStyles}>
            <Row lbl="URL" val={serverStatus.url}
                 element={<a href={serverStatus.url} target={"_blank"}>{serverStatus.url}</a> } />
            <Row lbl="" val="">
                <span className="lbl">Is Up?</span>
                {serverStatus.isUp ? <span className="val up">✅ Online</span> :
                    <span className="val down">❌ Offline</span>}
            </Row>
            <Row lbl="Status Code" val={serverStatus.responseCode}/>
            {serverStatus.responseTime && <Row lbl="Response Time" val={`${Math.round(serverStatus.responseTime)}ms`}/>}
        </Card>
    );
}

export default ServerStatusCard;
