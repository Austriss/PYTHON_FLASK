
const NewTag = () => {
        const [tagData, setTagData] = React.useState({label: ''})

    const handleEdit = (event) => {
        const newLabel = event.target.value;
        setTagData(previous => ({
                ...previous,
                label: newLabel
                }))
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
            try{
                const res = await fetch(`${baseUrl}tags/new`, {
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
    }

    return (
        <div>
            <h1> New tag </h1>
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
        const root = ReactDOM.createRoot(container);
        root.render(<NewTag />);
    } catch (error) {
        console.error(error);
    }
}