import IconForbidden from "@/assets/icons/icon-forbidden.svg?skipsvgo"
import IconInjection from "@/assets/icons/icon-injection.svg?skipsvgo"
import IconReordering from "@/assets/icons/icon-reordering.svg?skipsvgo"
export const VIOLATIONS_NAMES = {
    Censoring: 'censoring',
    Injection: 'injection',
    Reordering: 'reordering',
    Outlier: 'outlier',
}
export const VIOLATIONS_MAP = new Map([
    [VIOLATIONS_NAMES.Censoring, {
        title: VIOLATIONS_NAMES.Censoring,
        description: 'Blockchain node is censoring transactions.',
        icon: IconForbidden,
    }],
    [VIOLATIONS_NAMES.Injection, {
        title: VIOLATIONS_NAMES.Injection,
        description: 'Blockchain node is injecting transactions.',
        icon: IconInjection,
    }],
    [VIOLATIONS_NAMES.Reordering, {
        title: VIOLATIONS_NAMES.Reordering,
        description: 'Blockchain node is reordering transactions.',
        icon: IconReordering,
    }],
    [VIOLATIONS_NAMES.Outlier, {
        title: VIOLATIONS_NAMES.Outlier,
        description: 'Blockchain node is adding transactions out of nowhere at the last moment.',
        icon: IconReordering,
    }],
])
