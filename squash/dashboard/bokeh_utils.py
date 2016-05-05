from contextlib import closing
from bokeh.client import push_session, pull_session
from bokeh.document import Document
from bokeh.embed import autoload_server
from .viz.metrics import update_metric_data


def get_bokeh_script(user, plot, suffix):

    from .models import UserSession
    document = Document()
    document.add_root(plot)
    document.title = suffix

    with closing(push_session(document)) as session:
        # Save the session id
        UserSession.objects.create(user=user, bokehSessionId=session.id)
        # Get the script to pass into the template
        script = autoload_server(None, session_id=session.id)

    return script


def update_bokeh_sessions(user_sessions):
    for us in user_sessions:
        with closing(pull_session(session_id=us.bokehSessionId)) as session:
            if len(session.document.roots) == 0:
                # In this case, the session_id was from a dead session and
                # calling pull_session caused a new empty session to be
                # created. So we just delete the UserSession and move on.
                # It would be nice if there was a more efficient way - where I
                # could just ask bokeh if session x is a session.
                us.delete()
            else:
                # based on the document title we could decide which data to
                # update now we have just one
                update_metric_data(user=us.user, session=session)
