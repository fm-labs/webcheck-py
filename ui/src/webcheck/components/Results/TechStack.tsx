import styled from '@emotion/styled';
import {Card} from '@/webcheck/components/Form/Card.tsx';
import Heading from '@/webcheck/components/Form/Heading.tsx';
import colors from '@/webcheck/styles/colors.ts';
import type {JSX} from "react";

const cardStyles = `
  grid-row: span 2;
  small {
    margin-top: 1rem;
    opacity: 0.5;
    display: block;
    a { color: ${colors.primary}; }
  }
`;

const TechStackRow = styled.div`
    transition: all 0.2s ease-in-out;

    .r1 {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    h4 {
        margin: 0.5rem 0 0 0;
    }

    .r2 {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
    }

    .tech-version {
        opacity: 0.5;
    }

    .tech-confidence, .tech-categories {
        font-size: 0.8rem;
        opacity: 0.5;
    }

    .tech-confidence {
        display: none;
    }

    .tech-description, .tech-website {
        font-size: 0.8rem;
        margin: 0.25rem 0;
        font-style: italic;

        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;

        &.tech-website {
            -webkit-line-clamp: 1;
        }

        a {
            color: ${colors.primary};
            opacity: 0.75;

            &:hover {
                opacity: 1;
            }
        }
    }

    .tech-icon {
        min-width: 2.5rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }

    &:not(:last-child) {
        border-bottom: 1px solid ${colors.primaryTransparent};
    }

    &:hover {
        .tech-confidence {
            display: block;
        }

        .tech-categories {
            display: none;
        }
    }
`;

const TechStackCard = (props: { data: any, title: string, actionButtons: any }): JSX.Element => {
    if (!props.data || !props.data.technologies || props.data.technologies.length === 0) {
        return (
            <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
                <p>No technologies detected.</p>
            </Card>
        );
    }

    const technologies = props.data.technologies;
    const iconsCdn = 'https://www.wappalyzer.com/images/icons/';
    return (
        <Card heading={props.title} actionButtons={props.actionButtons} styles={cardStyles}>
            {Object.entries(technologies).map(([name, tech]: any, index: number) => {
                return (
                    <TechStackRow key={`tech-stack-row-${index}`}>
                        <div className="r1">
                            <Heading as="h4" size="small">
                                {name}
                                <span className="tech-version">{tech?.Version ? `(v${tech?.Version})` : ''}</span>
                            </Heading>
                            <span className="tech-confidence"
                                  title={`${tech?.Confidence || 0}% certain`}>Certainty: {tech?.Confidence || 0}%</span>
                            <span className="tech-categories">
              {tech?.Categories?.map((cat: any, i: number) => `${cat.name}${i < tech.Categories.length - 1 ? ', ' : ''}`)}
            </span>
                        </div>
                        <div className="r2">
                            <img className="tech-icon" width="10" src={`${iconsCdn}${tech.Icon}`} alt={name}/>
                            <div>
                                {tech?.Description && <p className="tech-description">{tech.Description}</p>}
                                {tech?.Website &&
                                    <p className="tech-website">Learn more at: <a href={tech.Website}>{tech.Website}</a>
                                    </p>}
                            </div>
                        </div>

                    </TechStackRow>
                );
            })}
        </Card>
    );
}

export default TechStackCard;
