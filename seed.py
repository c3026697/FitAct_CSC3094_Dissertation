"""
Database seeding script for FitAct.

Populates the database with all predefined data required for the application
to function. This script is idempotent — it checks for existing records before
inserting, so it can be safely re-run without creating duplicates.

Seeded in order:
    1. Exercises   — 24 exercises with muscle group and guidance text.
    2. Workouts    — 12 predefined workouts with associated exercises,
                     sets, reps, and exercise order.
    3. Programmes  — 5 training programmes (Full Body, Upper/Lower,
                     Push/Pull/Legs) with their workout schedules.
    4. Achievements — Milestone-based badges awarded during user activity.

Usage:
    python seed.py

Note:
    Requires the application to be configured with a valid DATABASE_URL.
    Run Flask-Migrate first to ensure all tables exist before seeding:
        flask db upgrade
        python seed.py
"""

from app import create_app
from app.extensions import db
from app.models import (
    Exercise,
    Workout,
    WorkoutExercise,
    Programme,
    ProgrammeWorkout,
    Achievement,
)

app = create_app()


def seed():
    with app.app_context():
        # ------------------------------------------------------------------ #
        # 1. EXERCISES
        # ------------------------------------------------------------------ #
        exercises_data = [
            # Upper Body A
            (
                "Bench Press",
                "Chest",
                "Lie flat on a bench. Grip the bar slightly wider than shoulder-width. Lower the bar to your mid-chest under control, then press back up to full extension. Keep your feet flat on the floor and your back naturally arched.",
            ),
            (
                "Bent-Over Row",
                "Back",
                "Hinge at the hips with a slight knee bend and hold the bar with an overhand grip. Pull the bar towards your lower chest, squeezing your shoulder blades together at the top. Lower under control.",
            ),
            (
                "Overhead Press",
                "Shoulders",
                "Stand with the bar at shoulder height, hands just outside shoulder-width. Press the bar directly overhead until your arms are fully extended. Lower it back to your shoulders with control.",
            ),
            (
                "Lat Pulldown",
                "Back",
                "Sit at a lat pulldown machine and grip the bar wider than shoulder-width. Pull the bar down to your upper chest while leaning back slightly. Squeeze your lats at the bottom, then return to the start slowly.",
            ),
            # Upper Body B
            (
                "Incline Dumbbell Press",
                "Chest",
                "Set a bench to 30–45 degrees. Hold dumbbells at chest height and press them upward until your arms are extended. Lower them slowly back to the start. Keep your core tight throughout.",
            ),
            (
                "Seated Cable Row",
                "Back",
                "Sit at a cable row station with feet on the platform. Pull the handle to your lower chest, keeping your elbows close to your body and your back upright. Return to the start under control.",
            ),
            (
                "Dumbbell Shoulder Press",
                "Shoulders",
                "Sit on an upright bench with dumbbells at shoulder height. Press both dumbbells overhead until your arms are extended. Lower them back to shoulder height in a controlled manner.",
            ),
            (
                "Assisted Pull-Up",
                "Back",
                "Use an assisted pull-up machine or resistance band for support. Grip the bar slightly wider than shoulder-width with an overhand grip. Pull yourself up until your chin clears the bar, then lower slowly.",
            ),
            # Lower Body A
            (
                "Back Squat",
                "Legs",
                "Position the bar across your upper traps. Stand with feet shoulder-width apart and toes slightly out. Lower yourself by bending your knees and hips until your thighs are parallel to the floor, then drive back up.",
            ),
            (
                "Romanian Deadlift",
                "Hamstrings",
                "Hold the bar in front of your thighs with a shoulder-width grip. Hinge at the hips, pushing them back as you lower the bar along your legs. Keep your back flat and lower until you feel a stretch in your hamstrings, then return to standing.",
            ),
            (
                "Walking Lunge",
                "Legs",
                "Stand tall holding dumbbells at your sides. Step forward with one leg and lower your back knee towards the floor, keeping your front knee over your ankle. Push through your front heel to bring your feet together, then step with the other leg.",
            ),
            (
                "Calf Raise",
                "Calves",
                "Stand on the edge of a step or flat ground with feet hip-width apart. Rise up on to your toes as high as possible, pause at the top, then lower your heels slowly below the step level for a full stretch.",
            ),
            # Lower Body B
            (
                "Leg Press",
                "Legs",
                "Sit in the leg press machine with feet shoulder-width apart on the platform. Lower the platform by bending your knees to around 90 degrees, then press back up to the start without locking your knees fully.",
            ),
            (
                "Hip Thrust",
                "Glutes",
                "Sit with your upper back against a bench, bar across your hips. Drive through your heels to thrust your hips upward until your body forms a straight line from shoulders to knees. Squeeze your glutes at the top, then lower.",
            ),
            (
                "Bulgarian Split Squat",
                "Legs",
                "Stand in front of a bench and place one foot behind you on it. Lower your back knee towards the floor while keeping your front shin as vertical as possible. Drive through your front heel to return to the start.",
            ),
            (
                "Hamstring Curl",
                "Hamstrings",
                "Lie face down on a leg curl machine. Curl your heels towards your glutes as far as possible, squeezing your hamstrings at the top. Lower the weight slowly back to the start.",
            ),
            # Push A
            (
                "Dumbbell Lateral Raise",
                "Shoulders",
                "Stand with dumbbells at your sides. Raise both arms out to the side until they are at shoulder height, keeping a slight bend in your elbows. Lower them back down slowly and under control.",
            ),
            # Push B
            (
                "Dumbbell Bench Press",
                "Chest",
                "Lie flat on a bench holding dumbbells at chest height with palms facing forward. Press both dumbbells up until your arms are extended, then lower them back to the start in a controlled arc.",
            ),
            (
                "Seated Dumbbell Shoulder Press",
                "Shoulders",
                "Sit on an upright bench holding dumbbells at shoulder height. Press both dumbbells overhead until your arms are extended. Lower them back to shoulder height with control.",
            ),
            (
                "Chest Press Machine",
                "Chest",
                "Sit in a chest press machine with handles at chest height. Press the handles forward until your arms are extended, then return to the start with control. Adjust the seat so your elbows are at 90 degrees at the start.",
            ),
            # Pull A
            (
                "Face Pull",
                "Shoulders",
                "Attach a rope to a cable machine at face height. Pull the rope towards your face, separating the ends as you pull. Keep your elbows high and squeeze your rear delts at the end of the movement.",
            ),
            # Pull B
            (
                "Pull-Up",
                "Back",
                "Hang from a bar with an overhand grip, hands slightly wider than shoulder-width. Pull yourself up until your chin clears the bar. Lower yourself slowly until your arms are fully extended.",
            ),
            (
                "One-Arm Dumbbell Row",
                "Back",
                "Place one hand and one knee on a bench for support. Hold a dumbbell with the other hand and row it up towards your hip, keeping your elbow close to your body. Lower it back down under control.",
            ),
            # Legs A/B extras
            (
                "Front Squat",
                "Legs",
                "Hold the bar across the front of your shoulders with elbows high. Stand with feet shoulder-width apart. Lower yourself by bending at the knees and hips until your thighs are parallel to the floor, then drive back up.",
            ),
        ]

        exercise_map = {}
        for name, muscle_group, guidance_text in exercises_data:
            existing = Exercise.query.filter_by(name=name).first()
            if not existing:
                ex = Exercise(
                    name=name, muscle_group=muscle_group, guidance_text=guidance_text
                )
                db.session.add(ex)
                db.session.flush()
                exercise_map[name] = ex
            else:
                exercise_map[name] = existing

        db.session.commit()
        print(f"✓ {len(exercise_map)} exercises seeded.")

        # ------------------------------------------------------------------ #
        # 2. WORKOUTS + WORKOUT EXERCISES
        # (sets_target, reps_target based on standard strength programming)
        # ------------------------------------------------------------------ #
        workouts_data = {
            "Upper Body A": {
                "type": "Upper",
                "exercises": [
                    ("Bench Press", 3, 8),
                    ("Bent-Over Row", 3, 8),
                    ("Overhead Press", 3, 8),
                    ("Lat Pulldown", 3, 10),
                ],
            },
            "Upper Body B": {
                "type": "Upper",
                "exercises": [
                    ("Incline Dumbbell Press", 3, 10),
                    ("Seated Cable Row", 3, 10),
                    ("Dumbbell Shoulder Press", 3, 10),
                    ("Assisted Pull-Up", 3, 8),
                ],
            },
            "Lower Body A": {
                "type": "Lower",
                "exercises": [
                    ("Back Squat", 4, 6),
                    ("Romanian Deadlift", 3, 8),
                    ("Walking Lunge", 3, 10),
                    ("Calf Raise", 3, 15),
                ],
            },
            "Lower Body B": {
                "type": "Lower",
                "exercises": [
                    ("Leg Press", 4, 10),
                    ("Hip Thrust", 3, 10),
                    ("Bulgarian Split Squat", 3, 8),
                    ("Hamstring Curl", 3, 12),
                ],
            },
            "Push A": {
                "type": "Push",
                "exercises": [
                    ("Bench Press", 4, 6),
                    ("Overhead Press", 3, 8),
                    ("Incline Dumbbell Press", 3, 10),
                    ("Dumbbell Lateral Raise", 3, 15),
                ],
            },
            "Pull A": {
                "type": "Pull",
                "exercises": [
                    ("Bent-Over Row", 4, 6),
                    ("Lat Pulldown", 3, 10),
                    ("Seated Cable Row", 3, 10),
                    ("Face Pull", 3, 15),
                ],
            },
            "Legs A": {
                "type": "Legs",
                "exercises": [
                    ("Back Squat", 4, 6),
                    ("Romanian Deadlift", 3, 8),
                    ("Leg Press", 3, 10),
                    ("Calf Raise", 3, 15),
                ],
            },
            "Push B": {
                "type": "Push",
                "exercises": [
                    ("Dumbbell Bench Press", 3, 10),
                    ("Seated Dumbbell Shoulder Press", 3, 10),
                    ("Chest Press Machine", 3, 12),
                    ("Dumbbell Lateral Raise", 3, 15),
                ],
            },
            "Pull B": {
                "type": "Pull",
                "exercises": [
                    ("Pull-Up", 3, 6),
                    ("One-Arm Dumbbell Row", 3, 10),
                    ("Seated Cable Row", 3, 10),
                    ("Face Pull", 3, 15),
                ],
            },
            "Legs B": {
                "type": "Legs",
                "exercises": [
                    ("Front Squat", 4, 6),
                    ("Hip Thrust", 3, 10),
                    ("Bulgarian Split Squat", 3, 8),
                    ("Hamstring Curl", 3, 12),
                ],
            },
        }

        # Full Body A = Upper Body A + Lower Body A exercises combined
        # Full Body B = Upper Body B + Lower Body B exercises combined
        workouts_data["Full Body A"] = {
            "type": "Full Body",
            "exercises": (
                workouts_data["Upper Body A"]["exercises"]
                + workouts_data["Lower Body A"]["exercises"]
            ),
        }
        workouts_data["Full Body B"] = {
            "type": "Full Body",
            "exercises": (
                workouts_data["Upper Body B"]["exercises"]
                + workouts_data["Lower Body B"]["exercises"]
            ),
        }

        workout_map = {}
        for workout_name, data in workouts_data.items():
            existing = Workout.query.filter_by(
                name=workout_name, is_custom=False
            ).first()
            if not existing:
                workout = Workout(name=workout_name, type=data["type"], is_custom=False)
                db.session.add(workout)
                db.session.flush()

                for order, (ex_name, sets, reps) in enumerate(
                    data["exercises"], start=1
                ):
                    we = WorkoutExercise(
                        workout_id=workout.id,
                        exercise_id=exercise_map[ex_name].id,
                        sets_target=sets,
                        reps_target=reps,
                        exercise_order=order,
                    )
                    db.session.add(we)

                workout_map[workout_name] = workout
            else:
                workout_map[workout_name] = existing

        db.session.commit()
        print(f"✓ {len(workout_map)} workouts seeded.")

        # ------------------------------------------------------------------ #
        # 3. PROGRAMMES + PROGRAMME WORKOUTS
        # ------------------------------------------------------------------ #
        programmes_data = [
            {
                "name": "2-Day Full Body",
                "split_type": "Full Body",
                "description": "A two-day full body programme ideal for beginners or those with limited time. Each session trains all major muscle groups.",
                "schedule": [
                    (1, "Full Body A"),
                    (2, "Full Body B"),
                ],
            },
            {
                "name": "3-Day Full Body",
                "split_type": "Full Body",
                "description": "A three-day full body programme suitable for beginners building a consistent training habit.",
                "schedule": [
                    (1, "Full Body A"),
                    (2, "Full Body B"),
                    (3, "Full Body A"),
                ],
            },
            {
                "name": "4-Day Upper / Lower",
                "split_type": "Upper/Lower",
                "description": "A four-day upper/lower split that trains each muscle group twice per week, suitable for intermediate lifters.",
                "schedule": [
                    (1, "Upper Body A"),
                    (2, "Lower Body A"),
                    (3, "Upper Body B"),
                    (4, "Lower Body B"),
                ],
            },
            {
                "name": "5-Day Upper / Lower + Full Body",
                "split_type": "Upper/Lower",
                "description": "A five-day programme combining upper/lower training with an additional full body session for increased volume.",
                "schedule": [
                    (1, "Upper Body A"),
                    (2, "Lower Body A"),
                    (3, "Upper Body B"),
                    (4, "Lower Body B"),
                    (5, "Full Body A"),
                ],
            },
            {
                "name": "6-Day Push / Pull / Legs",
                "split_type": "Push/Pull/Legs",
                "description": "A six-day push/pull/legs split for experienced lifters looking for high volume and frequency.",
                "schedule": [
                    (1, "Push A"),
                    (2, "Pull A"),
                    (3, "Legs A"),
                    (4, "Push B"),
                    (5, "Pull B"),
                    (6, "Legs B"),
                ],
            },
        ]

        for prog_data in programmes_data:
            existing = Programme.query.filter_by(name=prog_data["name"]).first()
            if not existing:
                programme = Programme(
                    name=prog_data["name"],
                    split_type=prog_data["split_type"],
                    description=prog_data["description"],
                )
                db.session.add(programme)
                db.session.flush()

                for order, (day_num, workout_name) in enumerate(
                    prog_data["schedule"], start=1
                ):
                    pw = ProgrammeWorkout(
                        programme_id=programme.id,
                        workout_id=workout_map[workout_name].id,
                        day_number=day_num,
                        workout_order=order,
                    )
                    db.session.add(pw)

        db.session.commit()
        print(f"✓ {len(programmes_data)} programmes seeded.")

        # ------------------------------------------------------------------ #
        # 4. ACHIEVEMENTS
        # ------------------------------------------------------------------ #
        achievements_data = [
            (
                "First Workout Completed",
                "You completed your very first workout on FitAct. The journey begins here!",
                "first_workout",
            ),
        ]

        for title, description, milestone_type in achievements_data:
            existing = Achievement.query.filter_by(
                milestone_type=milestone_type
            ).first()
            if not existing:
                achievement = Achievement(
                    title=title, description=description, milestone_type=milestone_type
                )
                db.session.add(achievement)

        db.session.commit()
        print(f"✓ {len(achievements_data)} achievements seeded.")

        print("\n✅ Database seeded successfully.")


if __name__ == "__main__":
    seed()
