
const EditTag = ({ tagId }) => {
    const [tagData, setTagData] = React.useState({tagId: 0, label: currentTag.label})

    const handleEdit = (event) => {
        const newLabel = event.target.value;
        setTagData(previous => ({
                ...previous,
                label: newLabel
                }))
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
            try {
                const res = await fetch(`${baseUrl}tags/update_tag/${tagId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        },
                    body: JSON.stringify(tagData),
                })
                window.location.href = `/tags/tags_list`;
            } catch (e) {
                console.error(e);
            }
    };
    return (
        <div>
            <h1> Editing tag </h1>
            <form onSubmit={handleSubmit} >
                <h2> Label </h2>
                <input
                    type="text"
                    id="label"
                    name="label"
                    value={tagData.label}
                    onChange={handleEdit}
                    required
                    />
                <div>
                    <button type="submit"> Submit </button>
                </div>
            </form>
        </div>
    );
}

const container = document.getElementById('root');
if (container) {
    try {
        const baseUrl = window.baseUrl;
        const currentTag = window.currentTag;
        const pathIntoParts = window.location.pathname.split("/");
        const urlTagId = pathIntoParts[pathIntoParts.length -1];
        const root = ReactDOM.createRoot(container);
        root.render(<EditTag tagId={urlTagId} currentTag={currentTag} baseUrl={baseUrl} />);
    } catch (error) {
        console.error(error);
    }
}