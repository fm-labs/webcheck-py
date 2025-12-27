import styled from '@emotion/styled';

import type { JSX, ReactNode } from "react";
import colors from "@/webcheck/styles/colors.ts";
import Heading from "@/webcheck/components/Form/Heading.tsx";

export const StyledCard = styled.section<{ styles?: string}>`
  //background: ${colors.backgroundLighter};
  //color: ${colors.textColor};
  border: 1px solid ${colors.primaryLighter};
  box-shadow: 4px 4px 0px ${colors.bgShadowColor};
  border-radius: 8px;
  padding: 1rem;
  position: relative;
  margin-bottom: 1rem;
  max-height: 64rem;
  max-width: 90vw;
  overflow: auto;
  ${props => props.styles}
`;

interface CardProps {
  children: ReactNode;
  heading?: string,
  styles?: string;
  actionButtons?: ReactNode | undefined;
};

export const Card = (props: CardProps): JSX.Element => {
  const { children, heading, styles, actionButtons } = props;
  return (
      <StyledCard styles={styles}>
        { actionButtons && actionButtons }
        { heading && <Heading align={"center"}>{heading}</Heading> }
        {children}
      </StyledCard>
  );
}

export default StyledCard;
