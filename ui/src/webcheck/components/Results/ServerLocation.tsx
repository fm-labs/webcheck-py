import type {JSX} from "react";
import styled from '@emotion/styled';
import type {ServerLocation} from '@/webcheck/utils/result-processor.ts';
import {Card} from '@/webcheck/components/Form/Card.tsx';
import Flag from '@/webcheck/components/misc/Flag.tsx';
import Row, {StyledRow} from '@/webcheck/components/Form/Row.tsx';
import LocationMap from "@/webcheck/components/misc/LocationMap.tsx";

const cardStyles = '';

const SmallText = styled.span`
    opacity: 0.5;
    text-align: right;
    display: block;
`;

const MapRow = styled(StyledRow)`
    padding-top: 1rem;
    flex-direction: column;
`;

const CountryValue = styled.span`
    display: flex;
    gap: 0.5rem;
`;

const ServerLocationCard = (props: { data: ServerLocation, title: string, actionButtons: any }): JSX.Element => {
    const location = props.data;
    if (!location) {
        return null;
    }

    console.log("Rendering ServerLocationCard with data:", location);

    // const location = {
    //     city: "Vienna",
    //     region: "Vienna",
    //     country: "Austria",
    //     postCode: "1010",
    //     countryCode: "AT",
    //     coords: {
    //         latitude: 48.2082,
    //         longitude: 16.3738,
    //     },
    //     isp: "Example ISP",
    //     timezone: "Europe/Vienna",
    //     languages: "German, English",
    //     currency: "Euro",
    //     currencyCode: "EUR",
    // }
    const {
        city, region, country,
        postCode, countryCode, coords,
        isp, timezone, languages, currency, currencyCode,
    } = location;

    return (
        <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
            <Row lbl="City" val={`${postCode}, ${city}, ${region}`}/>
            <Row lbl="" val="">
                <b>Country</b>
                <CountryValue>
                    {country}
                    {countryCode && <Flag countryCode={countryCode} width={28}/>}
                </CountryValue>
            </Row>
            <Row lbl="Timezone" val={timezone}/>
            <Row lbl="Languages" val={languages}/>
            <Row lbl="Currency" val={`${currency} (${currencyCode})`}/>
            {coords && <MapRow>
                <LocationMap lat={coords.latitude} lon={coords.longitude} label={`Server (${isp})`}/>
                <SmallText>Latitude: {coords.latitude}, Longitude: {coords.longitude} </SmallText>
            </MapRow>}
        </Card>
    );
}

export default ServerLocationCard;
