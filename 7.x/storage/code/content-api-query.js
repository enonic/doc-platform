var result = contentLib.query({
    start: 0,
    count: 2,
    query: "data.city = 'Oslo' AND fulltext('data.description', 'garden', 'AND') ",
    filters: {
        boolean: {
            must: {
                exists: {
                    field: "modifiedTime"
                }
            },
            mustNot: {
                hasValue: {
                    field: "myField",
                    values: [
                        "cheese",
                        "fish",
                        "onion"
                    ]
                }
            }
        },
        notExists: {
            field: "unwantedField"
        },
        ids: {
            values: ["id1", "id2"]
        }
    }
});
