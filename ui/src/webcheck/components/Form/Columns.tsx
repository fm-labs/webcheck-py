import styled from "@emotion/styled";
import type {JSX} from "react";


export const StyledColumns = styled.div`
  /* Default: mobile first */
  columns: 1; // 260px;   /* columns: <count> <width> */
  column-gap: 1rem;

  @media (min-width: 576px) {
    columns: 2; // 260px;
  }

  @media (min-width: 992px) {
    columns: 3; // 260px;
  }
`;

export const Columns = (props: { children: React.ReactNode }): JSX.Element => {
    const { children } = props;
    return (
        <StyledColumns>
            {children}
        </StyledColumns>
    );
}

export default Columns;