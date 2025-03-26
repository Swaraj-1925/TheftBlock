const MetricCard = ({ title, value }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6 text-center">
            <h3 className="text-xl font-bold mb-2">{title}</h3>
            <p className="text-3xl text-gray-500">{value}</p>
        </div>
    )
}

export default MetricCard

