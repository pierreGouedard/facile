# Global imports
import deform
import colander

class SeriesSchema(deform.schema.CSRFSchema):

    dateStart = colander.SchemaNode(
        colander.Date(),
        title="Date start")

    dateEnd = colander.SchemaNode(
        colander.Date(),
        title="Date end")

    tag = colander.SchemaNode(
        colander.String(),
        default='',
        title="Trafic category",
        description="key value arranged string")