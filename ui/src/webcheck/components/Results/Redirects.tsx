import colors from '@/webcheck/styles/colors.ts';
import { Card } from '@/webcheck/components/Form/Card.tsx';
import Row from '@/webcheck/components/Form/Row.tsx';
import type { JSX } from "react";

const cardStyles = `
  div {
    justify-content: flex-start;
    align-items: baseline; 
  }
  .arrow-thing {
    color: ${colors.primary};
    font-size: 1.8rem;
    font-weight: bold;
    margin-right: 0.5rem;
  }
  .redirect-count {
    color: ${colors.textColorSecondary};
    margin: 0;
  }
`;

const RedirectsCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
  const redirects = props.data;
  if (!redirects || !redirects?.redirects) {
    return (
      <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
        <Row lbl="" val="No data" />
      </Card>
    );
  }

  return (
    <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
      { !redirects?.redirects?.length && <Row lbl="" val="No redirects" />}
      <p className="redirect-count">
        Followed {redirects.redirects.length}{' '}
        redirect{redirects.redirects.length === 1 ? '' : 's'} when contacting host
      </p>
      {redirects.redirects.map((redirect: any, index: number) => {
        return (
          <Row lbl="" val="" key={index}>
          <span className="arrow-thing">↳</span> {redirect}
          </Row>
        );
      })}
    </Card>
  );
}

export default RedirectsCard;
