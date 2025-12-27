import { Card } from '@/webcheck/components/Form/Card.tsx';
import { ListRow }  from '@/webcheck/components/Form/Row.tsx';
import type { JSX } from "react";

const styles = `
  grid-row: span 2;
  .content {
    max-height: 50rem;
    overflow-x: hidden;
    overflow-y: auto;
  }
`;

const DnsRecordsCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
  const dnsRecords = props.data;
  return (
    <Card heading={props.title} actionButtons={props.actionButtons} styles={styles}>
      <div className="content">
      { dnsRecords.A && <ListRow title="A" list={dnsRecords.A} /> }
      { dnsRecords.AAAA?.length > 0 && <ListRow title="AAAA" list={dnsRecords.AAAA} /> }
      { dnsRecords.MX?.length > 0 && <ListRow title="MX" list={dnsRecords.MX} /> }
      { dnsRecords.CNAME?.length > 0 && <ListRow title="CNAME" list={dnsRecords.CNAME} /> }
      { dnsRecords.NS?.length > 0 && <ListRow title="NS" list={dnsRecords.NS} /> }
      { dnsRecords.PTR?.length > 0 && <ListRow title="PTR" list={dnsRecords.PTR} /> }
      { dnsRecords.SOA?.length > 0 && <ListRow title="SOA" list={dnsRecords.SOA} /> }
      { dnsRecords.TXT?.length > 0 && <ListRow title="TXT" list={dnsRecords.TXT} /> }
      </div>
    </Card>
  );
}

export default DnsRecordsCard;
