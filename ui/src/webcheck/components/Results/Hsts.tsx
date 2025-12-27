
import { Card } from '@/webcheck/components/Form/Card.tsx';
import Row, { type RowProps } from '@/webcheck/components/Form/Row.tsx';
import type { JSX } from "react";

const cardStyles = '';

const parseHeader = (headerString: string): RowProps[] => {
  return headerString.split(';').map((part) => {
    const trimmedPart = part.trim();
    const equalsIndex = trimmedPart.indexOf('=');

    if (equalsIndex >= 0) {
      return {
        lbl: trimmedPart.substring(0, equalsIndex).trim(),
        val: trimmedPart.substring(equalsIndex + 1).trim(),
      };
    } else {
      return { lbl: trimmedPart, val: 'true' };
    }
  });
};

const HstsCard = (props: {data: any, title: string, actionButtons: any }): JSX.Element => {
  const hstsResults = props.data;
  if (!hstsResults) {
    return null;
  }

  const hstsHeaders = hstsResults?.hstsHeader ? parseHeader(hstsResults.hstsHeader) : [];
  return (
    <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
      <Row lbl="HSTS Header" val={hstsResults?.hstsHeader} />
      <Row lbl="HSTS Enabled?" val={hstsResults.hstsHeader ? '✅ Yes' : '❌ No'} />
      {typeof hstsResults.compatible === 'boolean' && (
        <Row lbl="HSTS Compatible?" val={hstsResults.compatible ? '✅ Yes' : '❌ No'} />
      )}
      {hstsHeaders.length > 0 && hstsHeaders.map((header: RowProps, index: number) => {
        return (
          <Row lbl={header.lbl} val={header.val} key={`hsts-${index}`} />
        );
      })
      }

      {hstsResults.message && (<p>{hstsResults.message}</p>)}
    </Card>
  );
}

export default HstsCard;
