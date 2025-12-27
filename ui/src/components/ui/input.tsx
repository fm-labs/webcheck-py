import React, {type PropsWithChildren} from 'react';

export const Input = ({children, ...props}: PropsWithChildren<any>) => {
    return (
        <>
            <input {...props}>{children}</input>
        </>
    );
};

