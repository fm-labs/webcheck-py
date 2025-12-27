import { Card } from '@/webcheck/components/Form/Card.tsx';
import type { JSX } from "react";

const cardStyles = `
  overflow: auto;
  max-height: 50rem;
  grid-row: span 2;
  img {
    border-radius: 6px;
    width: 100%;
    margin 0.5rem 0;;
  }
`;

const SslQualysCard = (props: { data: { screenshot?: string, html?: string, }, title: string, actionButtons: any }): JSX.Element => {
  const qualys = props.data;
  return (
    <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
      { (qualys.screenshot) && <img src={qualys.screenshot} alt="Full page screenshot" /> }
      {/*{ (qualys.html) && <pre>{qualys.html}</pre> }*/}
    </Card>
  );
}

export default SslQualysCard;
