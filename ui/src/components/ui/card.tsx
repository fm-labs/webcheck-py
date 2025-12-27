import type {PropsWithChildren} from "react";


export const Card = (props: PropsWithChildren<any>) => {
    return (
        <div>
            {props.children}
        </div>
    )
}

export const CardTitle = (props: PropsWithChildren<any>) => {
    return (
        <div>
            {props.children}
        </div>
    )
}

export const CardContent = (props: PropsWithChildren<any>) => {
    return (
        <div>
            {props.children}
        </div>
    )
}

export const CardHeader = (props: PropsWithChildren<any>) => {
    return (
        <div>
            {props.children}
        </div>
    )
}