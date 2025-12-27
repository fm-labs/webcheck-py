import React, {type PropsWithChildren} from 'react';

export const Button = (props: PropsWithChildren<any>) => {
    return (
        <>
            <button className={props?.className}>{props.children}</button>
        </>
    );
};

export default Button;